from app.api.routes import MAX_BYTES
from conftest import workbook_bytes


def test_valid_full_flow(client, synthetic_frame):
    assert client.get('/api/health').json()['status'] == 'ok'
    data = workbook_bytes(synthetic_frame)
    response = client.post('/api/datasets/upload',files={'file':('SINTETIS_TEST.xlsx',data)})
    assert response.status_code == 200
    dataset_id = response.json()['id']
    base = f'/api/datasets/{dataset_id}'
    assert client.get(base+'/summary').json()['rows'] == 49
    assert client.get(base+'/quality').json()['puskesmas_mismatch_count'] == 0
    assert client.get(base+'/export/kmeans').status_code == 409
    for endpoint in ['preprocess','kmeans','regression']:
        assert client.post(base+'/'+endpoint,json={}).status_code == 200
        for format in ['csv','xlsx']:
            exported = client.get(base+f'/export/{endpoint}?format={format}')
            assert exported.status_code == 200 and len(exported.content)>0
    other_id = client.post('/api/datasets/upload',files={'file':('SINTETIS_TEST.xlsx',data)}).json()['id']
    assert other_id != dataset_id
    assert client.get(f'/api/datasets/{other_id}/export/kmeans').status_code == 409
    assert client.delete(base).status_code == 200
    assert client.get(base+'/summary').status_code == 404


def test_invalid_api(client, synthetic_frame):
    assert client.get('/api/datasets/absent/summary').status_code == 404
    assert client.post('/api/datasets/upload',files={'file':('bad.csv',b'abc')}).status_code == 415
    assert client.post('/api/datasets/upload',files={'file':('bad.xlsx',b'abc')}).status_code == 422
    assert client.post('/api/datasets/upload',files={'file':('big.xlsx',b'0'*(MAX_BYTES+1))}).status_code == 413
    data = workbook_bytes(synthetic_frame)
    dataset_id = client.post('/api/datasets/upload',files={'file':('SINTETIS_TEST.xlsx',data)}).json()['id']
    base = f'/api/datasets/{dataset_id}'
    assert client.post(base+'/kmeans',json={'k':8}).status_code == 422
    assert client.post(base+'/regression',json={'features':['Kemiskinan_Maret_Persen']}).status_code == 422
    assert client.post(base+'/regression',json={'train_years':[2025]}).status_code == 422
