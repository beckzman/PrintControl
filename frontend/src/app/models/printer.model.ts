export interface Printer {
    id: number;
    name: string;
    ip_address: string;
    model?: string;
    location?: string;
    status: string;
    last_updated?: Date;
    printer_type_id?: number;
    printer_type?: any;
    last_protocol?: string;
    sys_location?: string;
    sys_description?: string;
    last_web_crawl?: { content: string, timestamp: string };
    resolved_ip?: string; // Cache for DNS comparison
}

export interface ScanResponse {
    printer: Printer;
    reached: boolean;
}
