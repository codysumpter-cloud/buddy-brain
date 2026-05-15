import { SlugRegistry } from './slug-registry';
import { KnowledgeLinter } from '../core/linter/runner';
import { CompletenessPass, OrphansPass } from '../core/linter/passes';

export interface WriteRequest {
  title: string;
  content: string;
  evidence: string[];
  metadata: Record<string, any>;
  desiredSlug?: string;
}

export interface WriteResult {
  slug: string;
  status: 'created' | 'merged' | 'failed';
  conflictResolved: boolean;
  lintFindings?: any[];
}

export class BrainWriter {
  private linter: KnowledgeLinter;

  constructor(
    private registry: SlugRegistry,
    private storageEngine: any 
  ) {
    this.linter = new KnowledgeLinter([
      new CompletenessPass(),
      new OrphansPass()
    ]);
  }

  async write(request: WriteRequest, projectContext: { projectDir: string; outputDir: string; db?: any }): Promise<WriteResult> {
    // 1. Anti-Hallucination Check
    const isVerified = await this.verifyAgainstEvidence(request.content, request.evidence);
    if (!isVerified) {
      throw new Error('Content verification failed: BrainWriter detected potential hallucination.');
    }

    // 2. Slug Resolution
    const slugTarget = request.desiredSlug || request.title.toLowerCase().replace(/\s+/g, '-');
    const slugResult = await this.registry.create(slugTarget, request.title, 'page');

    // 3. Deterministic Persistence
    try {
      await this.storageEngine.savePage({
        slug: slugResult.slug,
        title: request.title,
        content: request.content,
        ...request.metadata
      });

      // 4. Post-Write Linting
      const lintResults = await this.linter.run({
        projectDir: projectContext.projectDir,
        outputDir: projectContext.outputDir,
        db: projectContext.db,
        dbPath: projectContext.projectDir + '/.sage/wiki.db',
        validRelations: [],
        validEntityTypes: []
      });
      
      const findings = lintResults.flatMap(r => r.findings);

      return {
        slug: slugResult.slug,
        status: slugResult.isConflict ? 'merged' : 'created',
        conflictResolved: slugResult.isConflict,
        lintFindings: findings
      };
    } catch (e) {
      console.error('Persistence failure in BrainWriter:', e);
      return { slug: slugResult.slug, status: 'failed', conflictResolved: false };
    }
  }

  private async verifyAgainstEvidence(content: string, evidence: string[]): Promise<boolean> {
    if (evidence.length === 0) return false;
    const evidenceKeywords = evidence.flatMap(e => e.split(/\s+/)).filter(w => w.length > 5);
    const matchCount = evidenceKeywords.filter(w => content.includes(w)).length;
    return matchCount > 0;
  }
}
