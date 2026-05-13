// Zod validation schemas for product forms
import { z } from 'zod';

export const ProductoFormSchema = z.object({
  nombre: z
    .string()
    .min(1, 'El nombre es obligatorio')
    .max(200, 'El nombre no puede exceder 200 caracteres'),
  descripcion: z.string().max(1000).nullable().optional(),
  precio_base: z
    .string()
    .regex(/^\d+(\.\d{1,2})?$/, 'El precio debe ser un número válido con hasta 2 decimales')
    .refine((val) => parseFloat(val) > 0, 'El precio debe ser mayor a 0'),
  stock_cantidad: z
    .number()
    .int('El stock debe ser un número entero')
    .min(0, 'El stock no puede ser negativo'),
  disponible: z.boolean().default(true),
  imagenes_url: z.string().url('Debe ser una URL válida').nullable().optional(),
  tiempo_prep_min: z
    .number()
    .int('Debe ser un número entero')
    .min(0, 'No puede ser negativo')
    .nullable()
    .optional(),
});

export type ProductoFormValues = z.infer<typeof ProductoFormSchema>;

export const StockUpdateSchema = z.object({
  cantidad: z
    .number()
    .int('La cantidad debe ser un número entero'),
});

export type StockUpdateValues = z.infer<typeof StockUpdateSchema>;
