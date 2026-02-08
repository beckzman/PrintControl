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
  protocol: 'SNMP' | 'WEB';
  discovery_config: any;
  vendor?: Vendor;
}

@Injectable({
  providedIn: 'root'
})
export class MasterDataService {
  private apiUrl = 'http://localhost:8001'; // Using 8001 as backend port

  constructor(private http: HttpClient) { }

  getVendors(): Observable<Vendor[]> {
    return this.http.get<Vendor[]>(`${this.apiUrl}/vendors/`);
  }

  createVendor(name: string): Observable<Vendor> {
    return this.http.post<Vendor>(`${this.apiUrl}/vendors/`, { name });
  }

  getPrinterTypes(): Observable<PrinterType[]> {
    return this.http.get<PrinterType[]>(`${this.apiUrl}/printer-types/`);
  }

  createPrinterType(type: Partial<PrinterType>): Observable<PrinterType> {
    return this.http.post<PrinterType>(`${this.apiUrl}/printer-types/`, type);
  }

  // --- Update & Delete Methods ---

  updateVendor(id: number, vendor: Partial<Vendor>): Observable<Vendor> {
    // Note: Backend might need an update endpoint, but for now we'll assume standard REST if implemented, 
    // or we might need to add it to backend. 
    // Wait, I only implemented create and get in backend for Vendors.
    // I need to check backend functionality first. 
    // Checking crud.py previously... I only saw get_vendor, get_vendors, create_vendor.
    // I need to add Update/Delete to backend first! 
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
