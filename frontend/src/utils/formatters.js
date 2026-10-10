/**
 * Formatting utilities for Indian Currency (INR, ₹) and Indian Number System
 * Complies with requirement to show all monetary amounts in Indian rupees (₹)
 * Examples: ₹1,25,000, ₹8,500, ₹12.5 lakh
 */

export function formatINR(val, options = {}) {
  if (val === null || val === undefined || val === '') return '₹0';
  
  let num;
  if (typeof val === 'number') {
    num = val;
  } else if (typeof val === 'string') {
    // If it's already an INR formatted string
    if (val.startsWith('₹')) return val;
    // Strip non-numeric chars except minus and period
    const cleaned = val.replace(/[^0-9.-]+/g, '');
    num = parseFloat(cleaned);
  } else {
    return '₹0';
  }

  if (isNaN(num)) return '₹0';

  const isNegative = num < 0;
  const absNum = Math.abs(num);

  // Compact representation when requested or for large values
  if (options.compact) {
    if (absNum >= 10000000) {
      const crVal = (absNum / 10000000).toFixed(2);
      return `${isNegative ? '-' : ''}₹${crVal} Cr`;
    }
    if (absNum >= 100000) {
      const lakhVal = (absNum / 100000).toFixed(options.decimals ?? 1);
      return `${isNegative ? '-' : ''}₹${lakhVal} lakh`;
    }
  }

  // Format with standard Indian numbering system (e.g., 1,25,000)
  const formatted = absNum.toLocaleString('en-IN', {
    maximumFractionDigits: options.decimals ?? 0,
    minimumFractionDigits: options.decimals ?? 0,
  });

  return `${isNegative ? '-' : ''}₹${formatted}`;
}

export function formatNumberIN(val, decimals = 0) {
  if (val === null || val === undefined) return '0';
  const num = typeof val === 'number' ? val : parseFloat(String(val).replace(/[^0-9.-]+/g, ''));
  if (isNaN(num)) return '0';
  return num.toLocaleString('en-IN', {
    maximumFractionDigits: decimals,
    minimumFractionDigits: decimals,
  });
}

export function formatPercent(val) {
  if (val === null || val === undefined) return '0%';
  const num = typeof val === 'number' ? val : parseFloat(String(val).replace(/[^0-9.-]+/g, ''));
  if (isNaN(num)) return '0%';
  return `${num.toFixed(1)}%`;
}
