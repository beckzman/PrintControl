export interface PrinterLog {
    id: number;
    printer_id: number;
    timestamp: string;
    event_type: string;
    old_value?: string;
    new_value?: string;
    message?: string;
}
