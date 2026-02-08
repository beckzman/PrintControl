export interface Printer {
    id: number;
    name: string;
    ip_address: string;
    model?: string;
    location?: string;
    status: string;
    last_updated?: Date;
    printer_type_id?: number;
    printer_type?: any; // Optional: Import PrinterType if needed, or use any to avoid circular dependency
}
