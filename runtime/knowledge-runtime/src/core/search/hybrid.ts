import { ResolverResult } from '../resolvers/interface.ts';

export interface SearchResult {
  slug: string;
  score: number;
  content: string;
  source: 'vector' | 'keyword' | 'both';
}

export class HybridSearchEngine {
  constructor(private vectorStore: any, private keywordStore: any) {}

  /**
   * Reciprocal Rank Fusion (RRF) to merge vector and keyword results.
   * score = Σ(1 / (k + rank))
   */
  async search(query: string, limit: number = 20): Promise<SearchResult[]> {
    const k = 60; // Standard RRF constant
    
    const [vectorResults, keywordResults] = await Promise.all([
      this.vectorStore.query(query, limit * 2),
      this.keywordStore.query(query, limit * 2)
    ]);

    const scores = new Map<string, number>();
    const resultsMap = new Map<string, any>();

    // Score vector results
    vectorResults.forEach((res: any, rank: number) => {
      const score = 1 / (k + rank + 1);
      scores.set(res.slug, (scores.get(res.slug) || 0) + score);
      resultsMap.set(res.slug, { ...res, source: 'vector' });
    });

    // Score keyword results
    keywordResults.forEach((res: any, rank: number) => {
      const score = 1 / (k + rank + 1);
      scores.set(res.slug, (scores.get(res.slug) || 0) + score);
      
      if (resultsMap.has(res.slug)) {
        resultsMap.get(res.slug).source = 'both';
      } else {
        resultsMap.set(res.slug, { ...res, source: 'keyword' });
      }
    });

    // Sort by fused score
    return Array.from(scores.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([slug, score]) => ({
        ...resultsMap.get(slug),
        slug,
        score
      }));
  }
}
