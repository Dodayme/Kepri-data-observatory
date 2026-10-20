export const API = import.meta.env.VITE_API_BASE || '/api'
export async function request<T>(path:string, init?:RequestInit):Promise<T> {
  const response=await fetch(API+path,init)
  if(!response.ok){let message=`Server merespons ${response.status}`;try{const body=await response.json();message=typeof body.detail==='string'?body.detail:JSON.stringify(body.detail)}catch{/* response non JSON */}throw new Error(message)}
  return response.json() as Promise<T>
}
export function post<T>(path:string,body:unknown={}) {return request<T>(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})}
