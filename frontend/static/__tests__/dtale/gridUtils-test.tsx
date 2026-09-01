import * as gu from '../../dtale/gridUtils';
import * as measureText from '../../dtale/MeasureText';
import { mockColumnDef } from '../mocks/MockColumnDef';

describe('gridUtils tests', () => {
  it('gridUtils: testing buildDataProps', () => {
    let dataProps = gu.buildDataProps(mockColumnDef({ name: 'foo', dtype: 'foo' }), 'bar', undefined);
    expect({ raw: 'bar', view: 'bar', style: {} }).toEqual(dataProps);
    dataProps = gu.buildDataProps(mockColumnDef({ name: 'foo', dtype: 'foo' }), undefined, undefined);
    expect(dataProps.view).toBe('');
  });

  it('gridUtils: calcColWidth resized', () => {
    expect(gu.calcColWidth(mockColumnDef({ resized: true, width: 100 }), {}, 1)).toEqual({
      width: 100,
    });
  });

  describe('maxColumnWidth', () => {
    let measureTextSpy: jest.SpyInstance;

    beforeEach(() => {
      measureTextSpy = jest.spyOn(measureText, 'measureText');
    });

    afterEach(jest.resetAllMocks);

    afterAll(jest.restoreAllMocks);

    it('column truncated', () => {
      measureTextSpy.mockImplementation(() => 150);
      expect(gu.calcColWidth(mockColumnDef(), {}, 1, undefined, undefined, 100)).toEqual({
        width: 100,
        dataWidth: 70,
        headerWidth: 150,
        resized: true,
      });
    });

    it('column unaffected', () => {
      measureTextSpy.mockImplementation(() => 50);
      expect(gu.calcColWidth(mockColumnDef(), {}, 1, undefined, undefined, 100)).toEqual({
        width: 70,
        dataWidth: 70,
        headerWidth: 50,
      });
    });
  });

  describe('headerRotation', () => {
    const columns = [
      mockColumnDef({ index: 0, visible: true }),
      mockColumnDef({ index: 1, width: 100, headerWidth: 100, dataWidth: 75, visible: true }),
    ];
    it('getColWidth defaults to horizontal when no rotation is given', () => {
      const width = gu.getColWidth(1, columns, undefined);
      expect(width).toEqual(100);
    });

    it('getColWidth w/ -90 (legacy verticalHeaders)', () => {
      const width = gu.getColWidth(1, columns, undefined, -90);
      expect(width).toEqual(75);
    });

    it('getColWidth w/ 45', () => {
      const width = gu.getColWidth(1, columns, undefined, 45);
      expect(width).toBeGreaterThan(75);
      expect(width).toBeLessThan(100 + gu.HEADER_HEIGHT);
    });

    it('getColWidth ignores rotation for resized columns', () => {
      const resizedColumns = [
        mockColumnDef({ index: 0, visible: true }),
        mockColumnDef({ index: 1, width: 120, headerWidth: 100, dataWidth: 75, resized: true, visible: true }),
      ];
      const width = gu.getColWidth(1, resizedColumns, undefined, -90);
      expect(width).toEqual(120);
    });

    it('getRowHeight', () => {
      let height = gu.getRowHeight(0, columns, undefined, undefined, -90);
      expect(height).toEqual(100);
      height = gu.getRowHeight(0, columns, undefined, undefined, 0);
      expect(height).toEqual(gu.HEADER_HEIGHT);
    });

    it('getRowHeight w/ 45', () => {
      const height = gu.getRowHeight(0, columns, undefined, undefined, 45);
      expect(height).toBeGreaterThan(gu.HEADER_HEIGHT);
      expect(height).toBeLessThan(100);
    });

    it('getHeaderRotation', () => {
      expect(gu.getHeaderRotation(undefined)).toEqual(0);
      expect(gu.getHeaderRotation({ verticalHeaders: false } as any)).toEqual(0);
      expect(gu.getHeaderRotation({ verticalHeaders: true } as any)).toEqual(-90);
      expect(gu.getHeaderRotation({ verticalHeaders: true, headerRotation: 45 } as any)).toEqual(45);
      expect(gu.getHeaderRotation({ verticalHeaders: true, headerRotation: 0 } as any)).toEqual(0);
      expect(gu.getHeaderRotation({ verticalHeaders: false, headerRotation: 45 } as any)).toEqual(45);
    });
  });
});
