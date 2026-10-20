from io import BytesIO
from pathlib import Path
from threading import RLock
from uuid import uuid4
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
import pandas as pd
from app.schemas.analysis import ClusterRequest, RegressionRequest
from app.services.preprocessing import read_workbook, quality, records, preprocess, KEYS, FEATURES
from app.services.clustering import cluster
from app.services.regression import regress

router = APIRouter(prefix='/api')
DATASETS = {}
LOCK = RLock()
MAX_BYTES = 10 * 1024 * 1024


def get_dataset(dataset_id):
    with LOCK:
        if dataset_id not in DATASETS:
            raise HTTPException(404, 'Dataset sesi tidak ditemukan. Unggah ulang setelah server dimulai ulang.')
        return DATASETS[dataset_id]


def register(content, name):
    try:
        frame = read_workbook(content)
    except Exception as exc:
        raise HTTPException(422, f'Workbook tidak dapat diproses: {exc}') from exc
    with LOCK:
        if len(DATASETS) >= 10:
            raise HTTPException(409, 'Batas 10 dataset sesi tercapai. Hapus dataset lama atau mulai ulang server.')
        dataset_id = uuid4().hex
        DATASETS[dataset_id] = {'frame': frame, 'name': name, 'results': {}}
    return {'id': dataset_id, 'filename': name, 'rows': len(frame), 'columns': len(frame.columns)}


@router.get('/health')
def health():
    return {'status': 'ok', 'storage': 'memory', 'max_upload_mb': 10}


@router.get('/reference')
def reference_info():
    root = Path(__file__).resolve().parents[3]
    files = sorted({*root.glob('Data_Sains*.xlsx'), *(root / 'data/input').glob('*.xlsx')})
    return {'files': [p.name for p in files]}


@router.post('/datasets/reference')
def load_reference():
    root = Path(__file__).resolve().parents[3]
    files = sorted({*root.glob('Data_Sains*.xlsx'), *(root / 'data/input').glob('*.xlsx')})
    if not files:
        raise HTTPException(404, 'Workbook lokal belum tersedia. Gunakan upload.')
    path = files[0]
    if path.stat().st_size > MAX_BYTES:
        raise HTTPException(413, 'File melebihi 10 MB.')
    return register(path.read_bytes(), path.name)


@router.post('/datasets/upload')
async def upload(file: UploadFile = File(...)):
    try:
        if not (file.filename or '').lower().endswith('.xlsx'):
            raise HTTPException(415, 'Hanya file .xlsx yang didukung.')
        content = await file.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise HTTPException(413, 'Ukuran unggahan maksimal 10 MB.')
        return register(content, Path(file.filename).name)
    finally:
        await file.close()


@router.delete('/datasets/{dataset_id}')
def delete(dataset_id: str):
    get_dataset(dataset_id)
    with LOCK:
        DATASETS.pop(dataset_id, None)
    return {'deleted': True}


@router.get('/datasets/{dataset_id}/summary')
def summary(dataset_id: str):
    item = get_dataset(dataset_id)
    frame = item['frame']
    return {'id': dataset_id, 'filename': item['name'], 'rows': len(frame), 'columns': frame.columns.tolist(), 'regions': sorted(frame[KEYS[0]].dropna().astype(str).unique().tolist()), 'years': sorted(pd.to_numeric(frame['Tahun'], errors='coerce').dropna().unique().tolist()), 'preview': records(frame), 'features': FEATURES}


@router.get('/datasets/{dataset_id}/quality')
def dataset_quality(dataset_id: str):
    return quality(get_dataset(dataset_id)['frame'])


def run(dataset_id, name, function, *args):
    item = get_dataset(dataset_id)
    try:
        result = function(item['frame'], *args)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    with LOCK:
        item['results'][name] = result
    return result


@router.post('/datasets/{dataset_id}/preprocess')
def preprocessing(dataset_id: str):
    return run(dataset_id, 'preprocess', preprocess)


@router.post('/datasets/{dataset_id}/kmeans')
def kmeans(dataset_id: str, config: ClusterRequest):
    return run(dataset_id, 'kmeans', cluster, config)


@router.post('/datasets/{dataset_id}/regression')
def regression(dataset_id: str, config: RegressionRequest):
    return run(dataset_id, 'regression', regress, config)


@router.get('/datasets/{dataset_id}/export/{analysis}')
def export(dataset_id: str, analysis: str, format: str = 'csv'):
    item = get_dataset(dataset_id)
    if analysis not in ['preprocess', 'kmeans', 'regression'] or format not in ['csv', 'xlsx']:
        raise HTTPException(422, 'Pilih analisis preprocess/kmeans/regression dan format csv/xlsx.')
    result = item['results'].get(analysis)
    if result is None:
        raise HTTPException(409, 'Jalankan analisis terlebih dahulu.')
    key = {'preprocess': 'engineered', 'kmeans': 'members', 'regression': 'predictions'}[analysis]
    frame = pd.DataFrame(result[key])
    if format == 'csv':
        content = frame.to_csv(index=False).encode('utf-8-sig')
        mime = 'text/csv'
    else:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            frame.to_excel(writer, index=False, sheet_name='Hasil')
            pd.DataFrame({'catatan': ['Hasil eksploratif; asosiasi bukan sebab-akibat.', 'Cluster bukan peringkat; data kesehatan belum terverifikasi.']}).to_excel(writer, index=False, sheet_name='Catatan')
        content = buffer.getvalue()
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return StreamingResponse(BytesIO(content), media_type=mime, headers={'Content-Disposition': f'attachment; filename="kepri-{analysis}.{format}"'})
