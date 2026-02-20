import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MasterDataService, Vendor, PrinterType } from '../../services/master-data';
import { PrinterService } from '../../services/printer.service';
import { Printer } from '../../models/printer.model';

@Component({
    selector: 'app-printer-list',
    standalone: true,
    imports: [CommonModule, FormsModule, RouterModule],
    templateUrl: './printer-list.component.html',
    styleUrls: ['./printer-list.component.css']
})
export class PrinterListComponent implements OnInit {
    printers: Printer[] = [];
    isLoading = false;
    editingPrinter: Printer | null = null;
    showDeleteConfirm = false;
    showLogs = false;
    selectedPrinterLogs: any[] = [];
    currentPrinterForLogs: any = null;
    showCrawl = false;
    currentCrawlContent = '';
    printerToDeleteId: number | null = null;
    newPrinter: Partial<Printer> = {};
    activePrinter: Printer | Partial<Printer> = {};
    selectedVendorId: number | undefined;
    viewMode: 'grid' | 'list' = 'list';
    searchTerm: string = '';
    showAddModal = false;
    notifications: { id: number, message: string, type: 'success' | 'error' | 'info' }[] = [];
    private nextNotificationId = 0;

    // Master Data
    vendors: Vendor[] = [];
    printerTypes: PrinterType[] = [];
    filteredPrinterTypes: PrinterType[] = [];

    get filteredPrinters(): Printer[] {
        if (!this.searchTerm) {
            return this.printers;
        }
        const term = this.searchTerm.toLowerCase();
        return this.printers.filter(printer =>
            printer.name.toLowerCase().includes(term) ||
            printer.ip_address.toLowerCase().includes(term) ||
            (printer.model && printer.model.toLowerCase().includes(term)) ||
            (printer.location && printer.location.toLowerCase().includes(term))
        );
    }

    constructor(
        private printerService: PrinterService,
        private masterDataService: MasterDataService
    ) { }

    ngOnInit(): void {
        this.loadPrinters();
        this.loadMasterData();
    }

    loadMasterData(): void {
        this.masterDataService.getVendors().subscribe(v => this.vendors = v);
        this.masterDataService.getPrinterTypes().subscribe(t => {
            this.printerTypes = t;
            // Only update filtered if we aren't already editing/adding which handles its own filtering
            if (!this.showAddModal && !this.editingPrinter) {
                this.filteredPrinterTypes = t;
            }
        });
    }

    onVendorChange(vendorId: any): void {
        const vId = vendorId === 'undefined' || vendorId === undefined || vendorId === null ? undefined : Number(vendorId);
        this.selectedVendorId = vId;

        if (vId) {
            this.filteredPrinterTypes = this.printerTypes.filter(pt => pt.vendor_id === vId);
        } else {
            this.filteredPrinterTypes = this.printerTypes;
        }

        // Reset printer type if it doesn't belong to new vendor
        const currentPrinter = this.activePrinter;
        if (currentPrinter.printer_type_id) {
            const type = this.printerTypes.find(t => t.id === currentPrinter.printer_type_id);
            if (type && type.vendor_id !== vId) {
                currentPrinter.printer_type_id = undefined;
            }
        }
    }

    // Helper to get vendor ID from printer type ID
    getVendorIdForPrinter(printer: Printer | Partial<Printer>): number | undefined {
        // Use type assertion or access as any if TS still complains, but model should have it
        const p = printer as any;
        if (!p.printer_type_id) return undefined;
        const type = this.printerTypes.find(t => t.id === p.printer_type_id);
        return type ? type.vendor_id : undefined;
    }

    getPrinterTypeName(printer: Printer | Partial<Printer>): string {
        const p = printer as any;
        if (!p.printer_type_id) return '';
        const type = this.printerTypes.find(t => t.id === p.printer_type_id);
        return type ? type.name : 'ID:' + p.printer_type_id;
    }

    loadPrinters(): void {
        this.isLoading = true;
        this.printerService.getPrinters().subscribe({
            next: (data) => {
                this.printers = data;
                this.isLoading = false;
                this.checkDnsMismatches();
            },
            error: (err) => {
                console.error('Error loading printers', err);
                this.isLoading = false;
            }
        });
    }

    scanPrinter(printer: Printer, protocol: string): void {
        this.isLoading = true;
        this.showNotification(`Starting ${protocol} scan for ${printer.ip_address}...`, 'info');

        this.printerService.scanPrinter(printer.id, protocol).subscribe({
            next: (response) => {
                const updatedPrinter = response.printer;
                const index = this.printers.findIndex(p => p.id === updatedPrinter.id);
                if (index !== -1) {
                    this.printers[index] = { ...this.printers[index], ...updatedPrinter };
                    this.printers = [...this.printers];
                }
                this.isLoading = false;

                if (response.reached) {
                    this.showNotification(`${protocol} scan successful for ${printer.name}!`, 'success');
                } else {
                    this.showNotification(`${protocol} scan completed, but device unreachable (Offline).`, 'error');
                }
            },
            error: (err) => {
                console.error('Error scanning printer', err);
                this.isLoading = false;
                this.showNotification(`${protocol} scan failed due to a system error.`, 'error');
            }
        });
    }

    showNotification(message: string, type: 'success' | 'error' | 'info'): void {
        const id = this.nextNotificationId++;
        this.notifications.push({ id, message, type });

        // Auto-remove after 4 seconds
        setTimeout(() => {
            this.notifications = this.notifications.filter(n => n.id !== id);
        }, 4000);
    }

    deletePrinter(id: number): void {
        if (confirm('Are you sure you want to delete this printer?')) {
            this.printerService.deletePrinter(id).subscribe(() => {
                this.printers = this.printers.filter(p => p.id !== id);
            });
        }
    }

    startEdit(printer: Printer): void {
        this.editingPrinter = { ...printer };
        this.activePrinter = this.editingPrinter;
        // Initialize selectedVendorId
        this.selectedVendorId = this.getVendorIdForPrinter(printer);

        const vendorId = this.selectedVendorId;
        if (vendorId) {
            this.filteredPrinterTypes = this.printerTypes.filter(pt => pt.vendor_id === vendorId);
        } else {
            this.filteredPrinterTypes = this.printerTypes;
        }
    }

    saveEdit(): void {
        if (this.editingPrinter) {
            this.printerService.updatePrinter(this.editingPrinter.id, this.editingPrinter).subscribe(updated => {
                const index = this.printers.findIndex(p => p.id === updated.id);
                if (index !== -1) {
                    this.printers[index] = updated;
                }
                this.editingPrinter = null;
                this.activePrinter = {};
                this.selectedVendorId = undefined;
            });
        }
    }

    cancelEdit(): void {
        this.editingPrinter = null;
        this.activePrinter = {};
        this.selectedVendorId = undefined;
    }

    openAddModal(): void {
        this.newPrinter = {};
        this.activePrinter = this.newPrinter;
        this.selectedVendorId = undefined;
        this.filteredPrinterTypes = this.printerTypes; // Show all types until vendor is picked
        this.showAddModal = true;
    }

    closeAddModal(): void {
        this.showAddModal = false;
        this.activePrinter = {};
        this.selectedVendorId = undefined;
    }

    isDetecting = false;

    detect(): void {
        const ip = this.activePrinter.ip_address;
        if (!ip) {
            alert('Please enter an IP address first');
            return;
        }

        this.isDetecting = true;
        this.printerService.detectPrinter(ip).subscribe({
            next: (result) => {
                this.isDetecting = false;
                if (result.online) {
                    const p = this.activePrinter as any;
                    if (result.model) p.model = result.model;
                    if (result.status) p.status = result.status;
                    if (result.vendor_id) {
                        this.selectedVendorId = result.vendor_id;
                        this.onVendorChange(this.selectedVendorId);
                    }
                    alert(`Detection successful!\nStatus: ${result.status}\nModel: ${result.model || 'Unknown'}\nMethod: ${result.protocol || 'Ping'}`);
                } else {
                    alert('Printer appears to be offline (Ping failed)');
                }
            },
            error: (err) => {
                this.isDetecting = false;
                console.error('Detection failed', err);
                alert('Detection failed: ' + JSON.stringify(err));
            }
        });
    }

    isResolving = false;

    resolveDNS(): void {
        const p = this.activePrinter as any;
        if (!p.name) {
            alert('Please enter a Name first to resolve');
            return;
        }

        this.isResolving = true;
        this.printerService.resolveHostname(p.name).subscribe({
            next: (result) => {
                this.isResolving = false;
                if (result.ip_address) {
                    p.ip_address = result.ip_address;
                    alert(`Resolved ${p.name} to ${result.ip_address}`);
                }
            },
            error: (err) => {
                this.isResolving = false;
                console.error('DNS Resolution failed', err);
                alert('DNS Resolution failed. Ensure the name is a valid hostname.');
            }
        });
    }

    checkDnsMismatches(): void {
        this.printers.forEach(printer => {
            if (printer.name) {
                this.printerService.resolveHostname(printer.name).subscribe({
                    next: (result) => {
                        printer.resolved_ip = result.ip_address;
                    },
                    error: () => {
                        printer.resolved_ip = undefined;
                    }
                });
            }
        });
    }

    isDnsMismatch(printer: Printer): boolean {
        return !!(printer.resolved_ip && printer.ip_address !== printer.resolved_ip);
    }

    viewLogs(printer: any): void {
        this.currentPrinterForLogs = printer;
        this.printerService.getPrinterLogs(printer.id).subscribe({
            next: (logs) => {
                this.selectedPrinterLogs = logs;
                this.showLogs = true;
            },
            error: (err) => {
                console.error('Error fetching logs', err);
                alert('Could not fetch history logs.');
            }
        });
    }

    closeLogs(): void {
        this.showLogs = false;
        this.selectedPrinterLogs = [];
        this.currentPrinterForLogs = null;
    }

    viewCrawl(printer: Printer): void {
        if (printer.last_web_crawl) {
            this.currentCrawlContent = printer.last_web_crawl.content;
            this.showCrawl = true;
        } else {
            alert('No web crawl data available for this printer.');
        }
    }

    closeCrawl(): void {
        this.showCrawl = false;
        this.currentCrawlContent = '';
    }

    createPrinter(): void {
        console.log('createPrinter called', this.activePrinter);
        const printer = this.activePrinter as Partial<Printer>;
        if (printer.name && printer.ip_address) {
            // Default status
            printer.status = 'Unknown';
            this.printerService.createPrinter(printer as any).subscribe({
                next: (created) => {
                    console.log('Printer created', created);
                    this.printers.push(created);
                    this.closeAddModal();
                },
                error: (err) => {
                    console.error('Error creating printer', err);
                    alert("Error creating printer: " + JSON.stringify(err));
                }
            });
        } else {
            console.warn('Validation failed', printer);
            alert('Please fill Name and IP Address');
        }
    }

    setViewMode(mode: 'grid' | 'list'): void {
        this.viewMode = mode;
    }

    getStatusTooltip(printer: Printer): string {
        const status = `Status: ${printer.status}`;
        const time = printer.last_updated ? new Date(printer.last_updated).toLocaleString() : 'Never';
        const protocol = printer.last_protocol || 'None';
        return `${status}\nLast Scan: ${time} via ${protocol}`;
    }
}
