import { EvidenceRubric, EvidencePiece, RubricResult } from './rubric';

export interface EnrichmentTask {
  entity: string;
  claims: string[];
  context: string;
}

export interface EnrichedEntity {
  entity: string;
  verifiedClaims: string[];
  contradictedClaims: string[];
  evidenceTrace: EvidencePiece[];
}

export class EnrichmentOrchestrator {
  constructor(private rubric: EvidenceRubric, private searchEngine: any) {}

  async enrich(task: EnrichmentTask): Promise<EnrichedEntity> {
    const verified: string[] = [];
    const contradicted: string[] = [];
    const allEvidence: EvidencePiece[] = [];

    for (const claim of task.claims) {
      // 1. Search for evidence related to the claim
      const results = await this.searchEngine.search(claim);
      const evidence: EvidencePiece[] = results.map((r: any) => ({
        source: r.url,
        text: r.content,
        confidence: r.score,
        timestamp: new Date()
      }));

      // 2. Evaluate against rubric
      const result: RubricResult = await this.rubric.evaluate(claim, evidence);
      
      if (result.verdict === 'verified') {
        verified.push(claim);
      } else if (result.verdict === 'contradicted') {
        contradicted.push(claim);
      }

      allEvidence.push(...evidence);
    }

    return {
      entity: task.entity,
      verifiedClaims: verified,
      contradictedClaims: contradicted,
      evidenceTrace: allEvidence
    };
  }
}
