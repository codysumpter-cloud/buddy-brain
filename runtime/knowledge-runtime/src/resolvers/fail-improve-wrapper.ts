import { Resolver, ResolverRequest, ResolverResult, ResolverContext } from './interface.ts';

export function wrapWithFailImprove(inner: Resolver<any, any>, fallbackResolverId: string, registry: any) {
  return {
    ...inner,
    async resolve(req: ResolverRequest<any>): Promise<ResolverResult<any>> {
      try {
        // 1. Try the deterministic path first
        return await inner.resolve(req);
      } catch (error) {
        console.log(`Deterministic resolve failed for ${inner.id}, falling back to ${fallbackResolverId}...`);
        
        // 2. Fallback to the LLM-based resolver (e.g. 'perplexity_query' or 'gpt-4o')
        const fallback = registry.get(fallbackResolverId);
        const result = await fallback.resolve({
          input: { 
            query: `The deterministic resolver ${inner.id} failed for input ${JSON.stringify(req.input)}. Please find the information and return it in the required schema.`,
            originalInput: req.input
          },
          context: req.context
        });
        
        return result;
      }
    }
  };
}
