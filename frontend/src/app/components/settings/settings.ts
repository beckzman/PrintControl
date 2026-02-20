import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { MasterDataService, Vendor, PrinterType } from '../../services/master-data';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './settings.html',
  styleUrls: ['./settings.css']
})
export class Settings implements OnInit {
  activeTab: 'printer-types' = 'printer-types';
  vendors: Vendor[] = [];
  printerTypes: PrinterType[] = [];

  // Vendor Form
  newVendorName = '';

  // Vendor Editing
  editingVendorId: number | null = null;
  editVendorName = '';

  // Printer Type Form
  newPrinterType: Partial<PrinterType> = {
    probes: ['ping', 'snmp'],
    discovery_config: '{}'
  };
  availableProbes = [
    { id: 'ping', label: 'Ping (Basic)' },
    { id: 'snmp', label: 'SNMP (Detailed)' },
    { id: 'web', label: 'Web Crawl' }
  ];
  configError = '';

  // Printer Type Editing
  editingTypeId: number | null = null;
  submitButtonText = 'Add Printer Type';

  constructor(
    private masterDataService: MasterDataService,
    private router: Router
  ) { }

  goBack(): void {
    this.router.navigate(['/']);
  }

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.masterDataService.getVendors().subscribe(data => this.vendors = data);
    this.masterDataService.getPrinterTypes().subscribe(data => this.printerTypes = data);
  }

  setActiveTab(tab: 'printer-types'): void {
    this.activeTab = tab;
    this.cancelEdit();
  }

  // --- Vendor Logic ---
  createVendor(): void {
    if (!this.newVendorName.trim()) return;
    this.masterDataService.createVendor(this.newVendorName).subscribe({
      next: (vendor) => {
        this.vendors.push(vendor);
        this.newVendorName = '';
      },
      error: (err) => alert('Failed to create vendor: ' + JSON.stringify(err))
    });
  }

  startEditVendor(vendor: Vendor): void {
    this.editingVendorId = vendor.id;
    this.editVendorName = vendor.name;
  }

  saveEditVendor(id: number): void {
    if (!this.editVendorName.trim()) return;
    this.masterDataService.updateVendor(id, { name: this.editVendorName }).subscribe({
      next: (updated) => {
        const index = this.vendors.findIndex(v => v.id === id);
        if (index !== -1) this.vendors[index] = updated;
        this.editingVendorId = null;
      },
      error: (err) => alert('Failed to update vendor: ' + JSON.stringify(err))
    });
  }

  cancelEditVendor(): void {
    this.editingVendorId = null;
    this.editVendorName = '';
  }

  deleteVendor(id: number): void {
    if (!confirm('Delete this vendor? This might affect printer types.')) return;
    this.masterDataService.deleteVendor(id).subscribe({
      next: () => {
        this.vendors = this.vendors.filter(v => v.id !== id);
      },
      error: (err) => alert('Failed to delete vendor: ' + JSON.stringify(err))
    });
  }

  // --- Printer Type Logic ---

  startEditPrinterType(type: PrinterType): void {
    this.editingTypeId = type.id;
    this.submitButtonText = 'Update Printer Type';
    this.newPrinterType = {
      vendor_id: type.vendor_id,
      name: type.name,
      probes: type.probes || [],
      discovery_config: JSON.stringify(type.discovery_config, null, 2) // Pretty print for editing
    };
    // Scroll to top to see form
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  cancelEdit(): void {
    this.editingTypeId = null;
    this.submitButtonText = 'Add Printer Type';
    this.newPrinterType = { probes: ['ping', 'snmp'], discovery_config: '{}' };
    this.configError = '';
  }

  handlePrinterTypeSubmit(): void {
    if (this.editingTypeId) {
      this.updatePrinterType();
    } else {
      this.createPrinterType();
    }
  }

  updatePrinterType(): void {
    if (!this.editingTypeId) return;
    const payload = this.preparePrinterTypePayload();
    if (!payload) return;

    this.masterDataService.updatePrinterType(this.editingTypeId, payload).subscribe({
      next: (updated) => {
        const index = this.printerTypes.findIndex(pt => pt.id === this.editingTypeId);
        if (index !== -1) {
          // Updated object might not have vendor joined, so we manually refresh or re-fetch
          this.printerTypes[index] = updated;
          this.loadData();
        }
        this.cancelEdit();
      },
      error: (err) => alert('Failed to update printer type: ' + JSON.stringify(err))
    });
  }

  createPrinterType(): void {
    const payload = this.preparePrinterTypePayload();
    if (!payload) return;

    this.masterDataService.createPrinterType(payload).subscribe({
      next: (type) => {
        this.printerTypes.push(type);
        this.loadData();
        this.cancelEdit();
      },
      error: (err) => alert('Failed to create printer type: ' + JSON.stringify(err))
    });
  }

  preparePrinterTypePayload(): any {
    if (!this.newPrinterType.name || !this.newPrinterType.vendor_id) {
      alert('Please fill in Name and Vendor');
      return null;
    }

    try {
      const config = typeof this.newPrinterType.discovery_config === 'string'
        ? JSON.parse(this.newPrinterType.discovery_config)
        : this.newPrinterType.discovery_config;

      this.configError = '';
      return { ...this.newPrinterType, discovery_config: config };
    } catch (e) {
      this.configError = 'Invalid JSON configuration';
      return null;
    }
  }

  deletePrinterType(id: number): void {
    if (!confirm('Delete this printer type?')) return;
    this.masterDataService.deletePrinterType(id).subscribe({
      next: () => {
        this.printerTypes = this.printerTypes.filter(pt => pt.id !== id);
      },
      error: (err) => alert('Failed to delete printer type: ' + JSON.stringify(err))
    });
  }

  isProbeEnabled(probeId: string): boolean {
    return (this.newPrinterType.probes || []).includes(probeId);
  }

  toggleProbe(probeId: string): void {
    const probes = [...(this.newPrinterType.probes || [])];
    const index = probes.indexOf(probeId);
    if (index > -1) {
      probes.splice(index, 1);
    } else {
      probes.push(probeId);
    }
    this.newPrinterType.probes = probes;
  }
}
