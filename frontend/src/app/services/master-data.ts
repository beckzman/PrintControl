import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Vendor {
  id: number;
  name: string;
}

export interface PrinterType {
  id: number;
  vendor_id: number;
  name: string;
  probes: string[];
  discovery_config: any;
  vendor?: Vendor;
}

@Injectable({
  providedIn: 'root'
})
export class MasterDataService {
  // Use relative path for proxy
  private apiUrl = '/api';

  constructor(private http: HttpClient) { }

  getVendors(): Observable<Vendor[]> {
    return this.http.get<Vendor[]>(`${this.apiUrl}/vendors`);
  }

  createVendor(name: string): Observable<Vendor> {
    return this.http.post<Vendor>(`${this.apiUrl}/vendors`, { name });
  }

  getPrinterTypes(): Observable<PrinterType[]> {
    return this.http.get<PrinterType[]>(`${this.apiUrl}/printer-types`);
  }

  createPrinterType(type: Partial<PrinterType>): Observable<PrinterType> {
    return this.http.post<PrinterType>(`${this.apiUrl}/printer-types`, type);
  }

  // --- Update & Delete Methods ---

  updateVendor(id: number, vendor: Partial<Vendor>): Observable<Vendor> {
    return this.http.put<Vendor>(`${this.apiUrl}/vendors/${id}`, vendor);
  }

  deleteVendor(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/vendors/${id}`);
  }

  updatePrinterType(id: number, type: Partial<PrinterType>): Observable<PrinterType> {
    return this.http.put<PrinterType>(`${this.apiUrl}/printer-types/${id}`, type);
  }

  deletePrinterType(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/printer-types/${id}`);
  }
}
