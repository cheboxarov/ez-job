const STORAGE_KEY_INPUT_PRICE = 'llm_token_input_price_per_million';
const STORAGE_KEY_OUTPUT_PRICE = 'llm_token_output_price_per_million';

const DEFAULT_INPUT_PRICE = 0;
const DEFAULT_OUTPUT_PRICE = 0;

export interface TokenPricing {
  inputPricePerMillion: number;
  outputPricePerMillion: number;
}

export const tokenPricingUtils = {
  getPricing: (): TokenPricing => {
    if (typeof window === 'undefined') {
      return {
        inputPricePerMillion: DEFAULT_INPUT_PRICE,
        outputPricePerMillion: DEFAULT_OUTPUT_PRICE,
      };
    }

    const inputPrice = localStorage.getItem(STORAGE_KEY_INPUT_PRICE);
    const outputPrice = localStorage.getItem(STORAGE_KEY_OUTPUT_PRICE);

    return {
      inputPricePerMillion: inputPrice ? parseFloat(inputPrice) : DEFAULT_INPUT_PRICE,
      outputPricePerMillion: outputPrice ? parseFloat(outputPrice) : DEFAULT_OUTPUT_PRICE,
    };
  },

  setPricing: (pricing: TokenPricing): void => {
    if (typeof window === 'undefined') {
      return;
    }

    localStorage.setItem(STORAGE_KEY_INPUT_PRICE, pricing.inputPricePerMillion.toString());
    localStorage.setItem(STORAGE_KEY_OUTPUT_PRICE, pricing.outputPricePerMillion.toString());
  },

  calculateCost: (
    promptTokens: number | null,
    completionTokens: number | null,
    pricing?: TokenPricing
  ): number | null => {
    const { inputPricePerMillion, outputPricePerMillion } = pricing || tokenPricingUtils.getPricing();

    if (promptTokens === null && completionTokens === null) {
      return null;
    }

    const promptCost =
      promptTokens !== null ? (promptTokens / 1_000_000) * inputPricePerMillion : 0;
    const completionCost =
      completionTokens !== null ? (completionTokens / 1_000_000) * outputPricePerMillion : 0;

    return promptCost + completionCost;
  },

  formatCost: (cost: number | null): string => {
    if (cost === null) {
      return '-';
    }
    if (cost < 0.01) {
      return `$${cost.toFixed(4)}`;
    }
    return `$${cost.toFixed(2)}`;
  },
};
