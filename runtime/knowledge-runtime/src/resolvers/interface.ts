export type ResolverCost = 'free' | 'rate-limited' | 'paid';

export interface ResolverRequest<I> {
  input: I;
  context: ResolverContext;
  timeoutMs?: number;
}

export interface ResolverResult<O> {
  value: O;
  confidence: number;
  source: string;
  fetchedAt: Date;
  costEstimate?: number;
  raw?: unknown;
}

export interface ResolverContext {
  engine: any; 
  storage: any;
  config: any;
  logger: any;
  metrics: any;
  budget: any;
  requestId: string;
  remote: boolean;
  deadline?: Date;
}

export interface Resolver<I, O> {
  readonly id: string;
  readonly cost: ResolverCost;
  readonly backend: string;
  readonly inputSchema: any;
  readonly outputSchema: any;

  available(ctx: ResolverContext): Promise<boolean>;
  resolve(req: ResolverRequest<I>): Promise<ResolverResult<O>>;
}
