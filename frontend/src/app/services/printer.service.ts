import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Printer, ScanResponse } from '../models/printer.model';

@Injectable({
    providedIn: 'root'
})
export class PrinterService {
    // Use localhost to match backend binding
    private apiUrl = 'http://localhost:8000/printers';

    constructor(private http: HttpClient) { }

    getPrinters(): Observable<Printer[]> {
        return this.http.get<Printer[]>(this.apiUrl);
    }

    getPrinter(id: number): Observable<Printer> {
        return this.http.get<Printer>(`${this.apiUrl}/${id}`);
    }

    createPrinter(printer: Omit<Printer, 'id' | 'status'>): Observable<Printer> {
        return this.http.post<Printer>(this.apiUrl, printer);
    }

    updatePrinter(id: number, printer: Partial<Printer>): Observable<Printer> {
        return this.http.put<Printer>(`${this.apiUrl}/${id}`, printer);
    }

    deletePrinter(id: number): Observable<Printer> {
        return this.http.delete<Printer>(`${this.apiUrl}/${id}`);
    }

    scanPrinter(id: number, protocol: string = 'snmp'): Observable<ScanResponse> {
        return this.http.post<ScanResponse>(`${this.apiUrl}/${id}/scan?protocol=${protocol}`, {});
    }

    detectPrinter(ip_address: string): Observable<any> {
        return this.http.post<any>(`${this.apiUrl}/detect`, { ip_address });
    }

    resolveHostname(hostname: string): Observable<{ ip_address: string }> {
        return this.http.post<{ ip_address: string }>(`${this.apiUrl}/resolve`, { hostname });
    }

    getPrinterLogs(id: number): Observable<any[]> {
        return this.http.get<any[]>(`${this.apiUrl}/${id}/logs`);
    }
}
