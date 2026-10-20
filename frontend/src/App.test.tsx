import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App, {Table} from './App'
import { request } from './api'

beforeEach(()=>{vi.restoreAllMocks()})
const show=(path='/')=>render(<MemoryRouter initialEntries={[path]}><App/></MemoryRouter>)
const response=(body:unknown,ok=true,status=200)=>({ok,status,json:async()=>body}) as Response
// SINTETIS_TEST: hanya fixture antarmuka, bukan observasi penelitian.
const summary={id:'synthetic-test',filename:'SINTETIS_TEST.xlsx',rows:1,columns:['Kabupaten_Kota','Tahun'],regions:['SINTETIS_TEST'],years:[2019],preview:[{Kabupaten_Kota:'SINTETIS_TEST',Tahun:2019,Kemiskinan_Maret_Persen:4}],features:[]}
const quality={issues:[],duplicates:[],invalid_keys:0,puskesmas_audit_available:true,puskesmas_mismatches:[],puskesmas_mismatch_count:0,outlier_signals:[],reference_match:false,warning:'ASLI bukan bukti verifikasi sumber resmi.',coverage_warning:'Cakupan berbeda.',zero_counts:{}}
function mockUpload(){vi.spyOn(globalThis,'fetch').mockImplementation(async(input)=>{const url=String(input);if(url.endsWith('/upload'))return response({id:'synthetic-test'});if(url.endsWith('/summary'))return response(summary);if(url.endsWith('/quality'))return response(quality);return response({detail:'Perhitungan gagal untuk fixture'},false,422)})}

describe('Antarmuka analisis',()=>{
  it('navigasi enam halaman dan empty state',()=>{show();expect(screen.getByText('Mulai dari data penelitian Anda')).toBeInTheDocument();for(const name of ['Data Preprocessing','K-Means Clustering','Linear Regression','Hasil Analisis','Upload Dataset','Dashboard']){fireEvent.click(screen.getByRole('link',{name}));expect(screen.getByRole('heading',{level:1,name})).toBeInTheDocument()}})
  it('upload berhasil menampilkan data API dan peringatan',async()=>{mockUpload();show('/upload');fireEvent.change(screen.getByLabelText('Upload workbook Excel'),{target:{files:[new File(['test'],'SINTETIS_TEST.xlsx')]}});await screen.findByText('Preview Master_Integrasi');expect(screen.getByText('ASLI bukan bukti verifikasi sumber resmi.')).toBeInTheDocument();expect(screen.getAllByText('SINTETIS_TEST').length).toBeGreaterThan(0);fireEvent.click(screen.getByRole('link',{name:'K-Means Clustering'}));const sd=screen.getByRole('checkbox',{name:'SD per 10.000 penduduk'});fireEvent.click(sd);expect(sd).toBeChecked();fireEvent.change(screen.getByRole('combobox'),{target:{value:'4'}});expect(screen.getByRole('combobox')).toHaveValue('4');fireEvent.click(screen.getByRole('button',{name:'Jalankan K-Means'}));expect(await screen.findByRole('alert')).toHaveTextContent('Perhitungan gagal')})
  it('upload gagal menampilkan error backend',async()=>{vi.spyOn(globalThis,'fetch').mockResolvedValue(response({detail:'Sheet Master_Integrasi tidak ditemukan.'},false,422));show('/upload');fireEvent.change(screen.getByLabelText('Upload workbook Excel'),{target:{files:[new File(['test'],'test.xlsx')]}});expect(await screen.findByRole('alert')).toHaveTextContent('Master_Integrasi')})
  it('menampilkan loading selama request tertunda',async()=>{let resolve!:(r:Response)=>void;vi.spyOn(globalThis,'fetch').mockImplementation(()=>new Promise(r=>{resolve=r}));show('/upload');fireEvent.click(screen.getByText('Baca workbook lokal'));expect(screen.getByText('Memproses data…')).toBeInTheDocument();resolve(response({detail:'Tidak tersedia'},false,404));await screen.findByRole('alert');await waitFor(()=>expect(screen.queryByText('Memproses data…')).not.toBeInTheDocument())})
  it('tabel merender baris dari respons API',()=>{render(<Table rows={[{wilayah:'SINTETIS_TEST',nilai:12}]}/>);expect(screen.getByRole('table')).toHaveTextContent('SINTETIS_TEST');expect(screen.getByRole('table')).toHaveTextContent('12')})
  it('request mengungkap kegagalan backend',async()=>{vi.spyOn(globalThis,'fetch').mockResolvedValue(response({detail:'Data tidak valid'},false,422));await expect(request('/datasets/x/summary')).rejects.toThrow('Data tidak valid')})
})
