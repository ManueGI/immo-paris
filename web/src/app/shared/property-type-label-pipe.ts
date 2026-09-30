import { Pipe, type PipeTransform } from '@angular/core';
import type { PropertyType } from '@immo-paris/api-client';

const LABELS: Record<PropertyType, string> = {
  apartment: 'Appartement',
  house: 'Maison',
};

/** Displays an API property type in French: {{ sale.property_type | propertyTypeLabel }} */
@Pipe({ name: 'propertyTypeLabel' })
export class PropertyTypeLabelPipe implements PipeTransform {
  transform(propertyType: PropertyType): string {
    return LABELS[propertyType];
  }
}
