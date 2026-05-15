export interface EvidencePiece {
  source: string;
  text: string;
  confidence: number;
  timestamp: Date;
}

export interface RubricResult {
  score: number;
  verdict: 'verified' | 'contradicted' | 'insufficient';
  reasoning: string;
}

export class EvidenceRubric {
  async evaluate(claim: string, evidence: EvidencePiece[]): Promise<RubricResult> {
    if (evidence.length === 0) {
      return { score: 0, verdict: 'insufficient', reasoning: 'No evidence provided.' };
    }

    // Weighted scoring based on confidence and source reliability
    let totalScore = 0;
    let matchCount = 0;

    for (const piece of evidence) {
      const match = this.checkMatch(claim, piece.text);
      if (match) {
        totalScore += piece.confidence;
        matchCount++;
      }
    }

    const averageScore = matchCount > 0 ? totalScore / evidence.length : 0;

    if (averageScore > 0.7) {
      return { score: averageScore, verdict: 'verified', reasoning: `Confirmed by ${matchCount} sources.` };
    } else if (averageScore > 0.3) {
      return { score: averageScore, verdict: 'insufficient', reasoning: 'Partial evidence found, but not definitive.' };
    } else {
      return { score: averageScore, verdict: 'contradicted', reasoning: 'Evidence does not support the claim.' };
    }
  }

  private checkMatch(claim: string, text: string): boolean {
    // Simplistic keyword overlap for demo purposes
    const claimWords = claim.toLowerCase().split(/\s+/).filter(w => w.length > 3);
    const textLower = text.toLowerCase();
    return claimWords.every(word => textLower.includes(word));
  }
}
