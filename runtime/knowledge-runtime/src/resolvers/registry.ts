import { Resolver, ResolverRequest, ResolverResult, ResolverContext } from './interface.ts';

export class ResolverRegistry {
  private resolvers = new Map<string, Resolver<any, any>>();

  register(resolver: Resolver<any, any>): void {
    this.resolvers.set(resolver.id, resolver);
  }

  get(id: string): Resolver<any, any> {
    const resolver = this.resolvers.get(id);
    if (!resolver) throw new Error(`Resolver ${id} not found`);
    return resolver;
  }

  list(filter?: { cost?: string; backend?: string }): Resolver<any, any>[] {
    return Array.from(this.resolvers.values()).filter(r => {
      if (filter?.cost && r.cost !== filter.cost) return false;
      if (filter?.backend && r.backend !== filter.backend) return false;
      return true;
    });
  }

  async resolve<I, O>(id: string, input: I, ctx: ResolverContext): Promise<ResolverResult<O>> {
    const resolver = this.get(id);
    return resolver.resolve({ input, context: ctx });
  }
}
