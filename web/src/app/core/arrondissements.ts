/** The 20 Paris arrondissements, identified in URLs by a readable slug ("paris-11"). */
export interface Arrondissement {
  /** 1 to 20 */
  readonly number: number;
  /** INSEE commune code used by the API: "75111" */
  readonly code: string;
  /** URL segment: "paris-11" */
  readonly slug: string;
  /** Display name: "Paris 11e" */
  readonly label: string;
}

export const ARRONDISSEMENTS: readonly Arrondissement[] = Array.from({ length: 20 }, (_, i) => {
  const number = i + 1;
  return {
    number,
    code: String(75100 + number),
    slug: `paris-${number}`,
    label: `Paris ${number}${number === 1 ? 'er' : 'e'}`,
  };
});

export function arrondissementBySlug(slug: string): Arrondissement | undefined {
  return ARRONDISSEMENTS.find((arrondissement) => arrondissement.slug === slug);
}

export function arrondissementByCode(code: string): Arrondissement | undefined {
  return ARRONDISSEMENTS.find((arrondissement) => arrondissement.code === code);
}
