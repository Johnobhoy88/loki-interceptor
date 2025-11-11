/**
 * Chart Export Utilities
 * Functions for exporting charts to PNG, SVG, and PDF formats
 */

import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { ExportOptions } from '@/types';

/**
 * Export a chart element to PNG
 */
export const exportToPNG = async (
  element: HTMLElement,
  options: ExportOptions = {}
): Promise<void> => {
  const {
    filename = 'chart.png',
    quality = 1.0,
    width,
    height,
    includeBackground = true,
  } = options;

  try {
    const canvas = await html2canvas(element, {
      backgroundColor: includeBackground ? '#ffffff' : null,
      scale: 2, // Higher resolution
      logging: false,
      width,
      height,
    });

    // Convert to blob and download
    canvas.toBlob(
      (blob) => {
        if (blob) {
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = filename;
          link.click();
          URL.revokeObjectURL(url);
        }
      },
      'image/png',
      quality
    );
  } catch (error) {
    console.error('Error exporting to PNG:', error);
    throw new Error('Failed to export chart to PNG');
  }
};

/**
 * Export a chart element to SVG
 */
export const exportToSVG = async (
  element: HTMLElement,
  options: ExportOptions = {}
): Promise<void> => {
  const { filename = 'chart.svg', includeBackground = true } = options;

  try {
    // Find SVG element within the container
    const svgElement = element.querySelector('svg');
    if (!svgElement) {
      throw new Error('No SVG element found in the container');
    }

    // Clone the SVG to avoid modifying the original
    const clonedSvg = svgElement.cloneNode(true) as SVGElement;

    // Add background if requested
    if (includeBackground) {
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('width', '100%');
      rect.setAttribute('height', '100%');
      rect.setAttribute('fill', 'white');
      clonedSvg.insertBefore(rect, clonedSvg.firstChild);
    }

    // Serialize SVG to string
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(clonedSvg);
    const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });

    // Download
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting to SVG:', error);
    throw new Error('Failed to export chart to SVG');
  }
};

/**
 * Export a chart element to PDF
 */
export const exportToPDF = async (
  element: HTMLElement,
  options: ExportOptions = {}
): Promise<void> => {
  const {
    filename = 'chart.pdf',
    quality = 0.95,
    width,
    height,
    includeBackground = true,
  } = options;

  try {
    // Convert to canvas first
    const canvas = await html2canvas(element, {
      backgroundColor: includeBackground ? '#ffffff' : null,
      scale: 2,
      logging: false,
      width,
      height,
    });

    // Calculate PDF dimensions
    const imgWidth = canvas.width;
    const imgHeight = canvas.height;
    const aspectRatio = imgWidth / imgHeight;

    // Create PDF with appropriate dimensions
    const pdfWidth = 210; // A4 width in mm
    const pdfHeight = pdfWidth / aspectRatio;

    const pdf = new jsPDF({
      orientation: aspectRatio > 1 ? 'landscape' : 'portrait',
      unit: 'mm',
      format: aspectRatio > 1 ? [pdfHeight, pdfWidth] : [pdfWidth, pdfHeight],
    });

    // Add image to PDF
    const imgData = canvas.toDataURL('image/jpeg', quality);
    pdf.addImage(
      imgData,
      'JPEG',
      0,
      0,
      aspectRatio > 1 ? pdfHeight : pdfWidth,
      aspectRatio > 1 ? pdfWidth : pdfHeight
    );

    // Save PDF
    pdf.save(filename);
  } catch (error) {
    console.error('Error exporting to PDF:', error);
    throw new Error('Failed to export chart to PDF');
  }
};

/**
 * Export multiple charts to a single PDF report
 */
export const exportMultipleChartsToPDF = async (
  elements: HTMLElement[],
  options: ExportOptions & { title?: string; description?: string } = {}
): Promise<void> => {
  const {
    filename = 'compliance-report.pdf',
    quality = 0.95,
    title = 'Compliance Analytics Report',
    description,
  } = options;

  try {
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const margin = 15;

    // Add title page
    pdf.setFontSize(24);
    pdf.text(title, margin, 30);

    if (description) {
      pdf.setFontSize(12);
      pdf.text(description, margin, 45, {
        maxWidth: pageWidth - 2 * margin,
      });
    }

    pdf.setFontSize(10);
    pdf.text(
      `Generated: ${new Date().toLocaleString()}`,
      margin,
      pageHeight - margin
    );

    // Add each chart on a new page
    for (let i = 0; i < elements.length; i++) {
      pdf.addPage();

      const canvas = await html2canvas(elements[i], {
        backgroundColor: '#ffffff',
        scale: 2,
        logging: false,
      });

      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const aspectRatio = imgWidth / imgHeight;

      // Calculate dimensions to fit on page
      let finalWidth = pageWidth - 2 * margin;
      let finalHeight = finalWidth / aspectRatio;

      if (finalHeight > pageHeight - 2 * margin) {
        finalHeight = pageHeight - 2 * margin;
        finalWidth = finalHeight * aspectRatio;
      }

      const imgData = canvas.toDataURL('image/jpeg', quality);
      const x = (pageWidth - finalWidth) / 2;
      const y = (pageHeight - finalHeight) / 2;

      pdf.addImage(imgData, 'JPEG', x, y, finalWidth, finalHeight);

      // Add page number
      pdf.setFontSize(10);
      pdf.text(
        `Page ${i + 2} of ${elements.length + 1}`,
        pageWidth / 2,
        pageHeight - margin,
        { align: 'center' }
      );
    }

    pdf.save(filename);
  } catch (error) {
    console.error('Error exporting multiple charts to PDF:', error);
    throw new Error('Failed to export charts to PDF');
  }
};

/**
 * Export chart data to CSV
 */
export const exportToCSV = (
  data: Record<string, any>[],
  filename: string = 'data.csv'
): void => {
  try {
    if (!data || data.length === 0) {
      throw new Error('No data to export');
    }

    // Get headers from first object
    const headers = Object.keys(data[0]);

    // Create CSV content
    const csvContent = [
      headers.join(','), // Header row
      ...data.map((row) =>
        headers.map((header) => {
          const value = row[header];
          // Escape values that contain commas or quotes
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      ),
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting to CSV:', error);
    throw new Error('Failed to export data to CSV');
  }
};

/**
 * Export chart data to JSON
 */
export const exportToJSON = (
  data: any,
  filename: string = 'data.json'
): void => {
  try {
    const jsonContent = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error exporting to JSON:', error);
    throw new Error('Failed to export data to JSON');
  }
};

/**
 * Copy chart element to clipboard as image
 */
export const copyToClipboard = async (
  element: HTMLElement,
  options: { includeBackground?: boolean } = {}
): Promise<void> => {
  const { includeBackground = true } = options;

  try {
    const canvas = await html2canvas(element, {
      backgroundColor: includeBackground ? '#ffffff' : null,
      scale: 2,
      logging: false,
    });

    // Convert canvas to blob
    return new Promise((resolve, reject) => {
      canvas.toBlob(async (blob) => {
        if (!blob) {
          reject(new Error('Failed to create image blob'));
          return;
        }

        try {
          await navigator.clipboard.write([
            new ClipboardItem({
              'image/png': blob,
            }),
          ]);
          resolve();
        } catch (error) {
          reject(error);
        }
      }, 'image/png');
    });
  } catch (error) {
    console.error('Error copying to clipboard:', error);
    throw new Error('Failed to copy chart to clipboard');
  }
};

export default {
  exportToPNG,
  exportToSVG,
  exportToPDF,
  exportMultipleChartsToPDF,
  exportToCSV,
  exportToJSON,
  copyToClipboard,
};
