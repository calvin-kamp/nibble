/** Response of a paginated DRF list endpoint (PageNumberPagination) */
export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
