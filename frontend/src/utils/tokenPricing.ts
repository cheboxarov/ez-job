export const tokenPricingUtils = {
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
