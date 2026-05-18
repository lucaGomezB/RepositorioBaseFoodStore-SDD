// Payment Store tests
import { describe, it, expect, beforeEach } from 'vitest';
import { usePaymentStore } from '../paymentStore';

describe('paymentStore', () => {
  beforeEach(() => {
    // Reset store to initial state
    usePaymentStore.setState({
      paymentMethod: null,
      paymentStatus: 'pending',
      preferenceId: null,
      preferenceUrl: null,
      cardToken: null,
      orderId: null,
      orderTotal: 0,
      lastError: null,
    });
    localStorage.clear();
  });

  it('should start with default state', () => {
    const state = usePaymentStore.getState();
    expect(state.paymentMethod).toBeNull();
    expect(state.paymentStatus).toBe('pending');
    expect(state.preferenceId).toBeNull();
    expect(state.preferenceUrl).toBeNull();
    expect(state.cardToken).toBeNull();
    expect(state.orderId).toBeNull();
    expect(state.orderTotal).toBe(0);
    expect(state.lastError).toBeNull();
  });

  it('should set payment method and clear error', () => {
    usePaymentStore.getState().setPaymentMethod('card');
    const state = usePaymentStore.getState();
    expect(state.paymentMethod).toBe('card');
    expect(state.lastError).toBeNull();
  });

  it('should set payment status', () => {
    usePaymentStore.getState().setPaymentStatus('approved');
    expect(usePaymentStore.getState().paymentStatus).toBe('approved');
  });

  it('should set preference data and reset status to pending', () => {
    usePaymentStore.getState().setPaymentStatus('approved');
    usePaymentStore.getState().setPreference('pref-123', 'https://mp.com/pay/123');

    const state = usePaymentStore.getState();
    expect(state.preferenceId).toBe('pref-123');
    expect(state.preferenceUrl).toBe('https://mp.com/pay/123');
    expect(state.paymentStatus).toBe('pending');
  });

  it('should clear preference', () => {
    usePaymentStore.getState().setPreference('pref-123', 'https://mp.com/pay/123');
    usePaymentStore.getState().clearPreference();

    const state = usePaymentStore.getState();
    expect(state.preferenceId).toBeNull();
    expect(state.preferenceUrl).toBeNull();
  });

  it('should set and clear card token', () => {
    usePaymentStore.getState().setCardToken('tok-test-abc');
    expect(usePaymentStore.getState().cardToken).toBe('tok-test-abc');

    usePaymentStore.getState().clearCardToken();
    expect(usePaymentStore.getState().cardToken).toBeNull();
  });

  it('should set order data and reset status', () => {
    usePaymentStore.getState().setPaymentStatus('approved');
    usePaymentStore.getState().setOrder(42, 150.00);

    const state = usePaymentStore.getState();
    expect(state.orderId).toBe(42);
    expect(state.orderTotal).toBe(150.00);
    expect(state.paymentStatus).toBe('pending');
    expect(state.lastError).toBeNull();
  });

  it('should clear order data', () => {
    usePaymentStore.getState().setOrder(42, 150.00);
    usePaymentStore.getState().clearOrder();

    const state = usePaymentStore.getState();
    expect(state.orderId).toBeNull();
    expect(state.orderTotal).toBe(0);
  });

  it('should set error and reject payment status', () => {
    usePaymentStore.getState().setError('Payment declined');

    const state = usePaymentStore.getState();
    expect(state.lastError).toBe('Payment declined');
    expect(state.paymentStatus).toBe('rejected');
  });

  it('should reset all payment state', () => {
    usePaymentStore.getState().setPaymentMethod('card');
    usePaymentStore.getState().setPreference('pref-123', 'https://mp.com/pay');
    usePaymentStore.getState().setOrder(42, 150.00);

    usePaymentStore.getState().resetPayment();

    const state = usePaymentStore.getState();
    expect(state.paymentMethod).toBeNull();
    expect(state.paymentStatus).toBe('pending');
    expect(state.preferenceId).toBeNull();
    expect(state.preferenceUrl).toBeNull();
    expect(state.cardToken).toBeNull();
    expect(state.orderId).toBeNull();
    expect(state.orderTotal).toBe(0);
    expect(state.lastError).toBeNull();
  });
});
