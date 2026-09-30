import { ARRONDISSEMENTS, arrondissementByCode, arrondissementBySlug } from './arrondissements';

describe('arrondissements', () => {
  it('lists the 20 Paris arrondissements with their INSEE codes', () => {
    expect(ARRONDISSEMENTS).toHaveLength(20);
    expect(ARRONDISSEMENTS[0]).toEqual({
      number: 1,
      code: '75101',
      slug: 'paris-1',
      label: 'Paris 1er',
    });
    expect(ARRONDISSEMENTS[19]?.label).toBe('Paris 20e');
  });

  it('finds an arrondissement by slug or by code', () => {
    expect(arrondissementBySlug('paris-11')?.code).toBe('75111');
    expect(arrondissementByCode('75111')?.slug).toBe('paris-11');
  });

  it('returns undefined for unknown slugs and codes', () => {
    expect(arrondissementBySlug('paris-21')).toBeUndefined();
    expect(arrondissementBySlug('75111')).toBeUndefined();
    expect(arrondissementByCode('69381')).toBeUndefined();
  });
});
