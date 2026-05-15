export interface CreatedSlug {
  slug: string;
  isConflict: boolean;
  originalDesired: string;
}

export class SlugRegistry {
  constructor(private engine: any) {}

  async create(desiredSlug: string, displayName: string, type: string): Promise<CreatedSlug> {
    // In a real impl, this would query the DB for existing slugs
    const exists = await this.engine.pageExists(desiredSlug);
    if (!exists) {
      return { slug: desiredSlug, isConflict: false, originalDesired: desiredSlug };
    }

    // Basic disambiguation: append a random suffix or counter
    const disambiguated = `${desiredSlug}-${Math.floor(Math.random() * 1000)}`;
    return { slug: disambiguated, isConflict: true, originalDesired: desiredSlug };
  }

  async confirmSame(slugA: string, slugB: string, confidence: number): Promise<void> {
    if (confidence < 0.8) {
      throw new Error(`Insufficient confidence (${confidence}) to merge ${slugA} and ${slugB}`);
    }
  }

  async merge(canonical: string, duplicate: string): Promise<void> {
    await this.engine.updateRedirect(duplicate, canonical);
  }
}
