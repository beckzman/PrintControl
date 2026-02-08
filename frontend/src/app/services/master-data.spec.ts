import { TestBed } from '@angular/core/testing';

import { MasterData } from './master-data';

describe('MasterData', () => {
  let service: MasterData;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(MasterData);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
