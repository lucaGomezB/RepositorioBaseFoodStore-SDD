// Payment Store - State-only (checkout flow state)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type PaymentMethod = 'card' | 'account_money' | 'ticket';
export type PaymentStatus = 'pending' | 'processing' | 'approved' | 'rejected' | 'cancelled';

export interface PaymentState {
  // Checkout flow
  paymentMethod: PaymentMethod | null;
  paymentStatus: PaymentStatus;
  
  // MercadoPago data
  preferenceId: string | null;
  preferenceUrl: string | null;
  
  // Card data (temporary, not persisted for security)
  cardToken: string | null;
  
  // Order reference
  orderId: number | null;
  orderTotal: number;
  
  // Error handling
  lastError: string | null;
}

export interface PaymentActions {
  setPaymentMethod: (method: PaymentMethod) => void;
  setPaymentStatus: (status: PaymentStatus) => void;
  
  setPreference: (id: string, url: string) => void;
  clearPreference: () => void;
  
  setCardToken: (token: string) => void;
  clearCardToken: () => void;
  
  setOrder: (orderId: number, total: number) => void;
  clearOrder: () => void;
  
  setError: (error: string | null) => void;
  resetPayment: () => void;
}

type PaymentStore = PaymentState & PaymentActions;

export const usePaymentStore = create<PaymentStore>()(
  persist(
    (set) => ({
      // Initial state
      paymentMethod: null,
      paymentStatus: 'pending',
      preferenceId: null,
      preferenceUrl: null,
      cardToken: null,
      orderId: null,
      orderTotal: 0,
      lastError: null,

      // Actions
      setPaymentMethod: (method) => {
        set({ 
          paymentMethod: method,
          lastError: null,
        });
      },

      setPaymentStatus: (status) => {
        set({ paymentStatus: status });
      },

      setPreference: (id, url) => {
        set({
          preferenceId: id,
          preferenceUrl: url,
          paymentStatus: 'pending',
        });
      },

      clearPreference: () => {
        set({
          preferenceId: null,
          preferenceUrl: null,
        });
      },

      setCardToken: (token) => {
        set({ cardToken: token });
      },

      clearCardToken: () => {
        set({ cardToken: null });
      },

      setOrder: (orderId, total) => {
        set({
          orderId,
          orderTotal: total,
          paymentStatus: 'pending',
          lastError: null,
        });
      },

      clearOrder: () => {
        set({
          orderId: null,
          orderTotal: 0,
        });
      },

      setError: (error) => {
        set({ 
          lastError: error,
          paymentStatus: 'rejected',
        });
      },

      resetPayment: () => {
        set({
          paymentMethod: null,
          paymentStatus: 'pending',
          preferenceId: null,
          preferenceUrl: null,
          cardToken: null,
          orderId: null,
          orderTotal: 0,
          lastError: null,
        });
      },
    }),
    {
      name: 'payment-storage',
      partialize: (state) => ({
        // Only persist preference data for resume after reload
        preferenceId: state.preferenceId,
        preferenceUrl: state.preferenceUrl,
        orderId: state.orderId,
        orderTotal: state.orderTotal,
        paymentStatus: state.paymentStatus,
      }),
    }
  )
);

// Convenience selectors
export const selectPaymentMethod = (state: PaymentStore) => state.paymentMethod;
export const selectPaymentStatus = (state: PaymentStore) => state.paymentStatus;
export const selectPreference = (state: PaymentStore) => ({
  id: state.preferenceId,
  url: state.preferenceUrl,
});
export const selectOrder = (state: PaymentStore) => ({
  id: state.orderId,
  total: state.orderTotal,
});
export const selectHasError = (state: PaymentStore) => state.lastError !== null;