import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize('headers', [{'Idempotency-Key': 'abc123'}])
async def test_basic_idempotency(backend, sync_client, async_client, headers):
    payload = {'message': 'hello'}

    if async_client:
        resp1 = await async_client.post('/echo', json=payload, headers=headers)
        resp2 = await async_client.post('/echo', json=payload, headers=headers)
    else:
        resp1 = sync_client.post('/echo', json=payload, headers=headers)
        resp2 = sync_client.post('/echo', json=payload, headers=headers)

    assert resp1.status_code == 200
    assert resp1.json() == {'echo': payload}
    assert resp2.status_code == 200
    assert resp2.json() == {'echo': payload}


@pytest.mark.asyncio
async def test_missing_idempotency_key(backend, sync_client, async_client):
    payload = {'message': 'no key'}

    if async_client:
        resp = await async_client.post('/echo', json=payload)
    else:
        resp = sync_client.post('/echo', json=payload)

    assert resp.status_code == 400
    assert resp.json()['detail'] == 'Missing Idempotency-Key'


@pytest.mark.asyncio
async def test_same_key_different_payload_raises_conflict(backend, sync_client, async_client):
    headers = {'Idempotency-Key': 'same-key'}
    payload1 = {'x': 1}
    payload2 = {'x': 999}

    if async_client:
        resp1 = await async_client.post('/echo', json=payload1, headers=headers)
        resp2 = await async_client.post('/echo', json=payload2, headers=headers)
    else:
        resp1 = sync_client.post('/echo', json=payload1, headers=headers)
        resp2 = sync_client.post('/echo', json=payload2, headers=headers)

    assert resp1.status_code == 200
    assert resp2.status_code == 409
    assert 'does not match' in resp2.json()['detail']
