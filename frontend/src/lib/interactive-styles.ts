/**
 * Focus ring for borderless or flush-bordered controls
 * (input, textarea, select trigger).
 * The ring sits directly on the field edge — no offset.
 */
export const focusRing =
  'outline-hidden focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-3'

/**
 * Offset focus ring for solid controls (button, checkbox, radio,
 * card radio, stepper). The offset is applied under `focus-visible`
 * only, never globally.
 */
export const focusRingOffset =
  'outline-hidden focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-3 focus-visible:ring-offset-2 focus-visible:ring-offset-background'

/** Focus ring for destructive actions (button variant `destructive`). */
export const focusRingDestructive =
  'outline-hidden focus-visible:border-destructive/40 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 focus-visible:ring-3 focus-visible:ring-offset-2 focus-visible:ring-offset-background'

/**
 * Focus ring for wrappers whose inner control holds the focus
 * (InputGroup, NumberFieldContent). The wrapper shows the ring as soon
 * as the control marked `data-slot="input-group-control"` or
 * `data-slot="number-field-input"` is focused — the control itself
 * gives up its own ring via `focusRingReset`. Addon and stepper buttons
 * inside the wrapper deliberately do not trigger the group ring;
 * they have their own.
 */
export const focusRingWithin =
  'outline-hidden has-[[data-slot=input-group-control]:focus-visible]:border-ring has-[[data-slot=input-group-control]:focus-visible]:ring-ring/50 has-[[data-slot=input-group-control]:focus-visible]:ring-3 has-[[data-slot=number-field-input]:focus-visible]:border-ring has-[[data-slot=number-field-input]:focus-visible]:ring-ring/50 has-[[data-slot=number-field-input]:focus-visible]:ring-3'

/**
 * Removes focus and error ring from embedded controls whose wrapper
 * handles the visual state (InputGroupInput, InputGroupTextarea).
 */
export const focusRingReset = 'focus-visible:ring-0 aria-invalid:ring-0'

/**
 * Error state via `aria-invalid`. Colour is never the sole carrier of
 * meaning here — the matching FieldError message adds icon and text.
 */
export const invalidRing =
  'aria-invalid:border-destructive dark:aria-invalid:border-destructive/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:ring-3'

/**
 * Error state on the wrapper when the embedded control carries
 * `aria-invalid` (counterpart to `focusRingWithin`).
 */
export const invalidRingWithin =
  'has-[[data-slot][aria-invalid=true]]:border-destructive dark:has-[[data-slot][aria-invalid=true]]:border-destructive/50 has-[[data-slot][aria-invalid=true]]:ring-destructive/20 dark:has-[[data-slot][aria-invalid=true]]:ring-destructive/40 has-[[data-slot][aria-invalid=true]]:ring-3'

/**
 * Focus state for menu and list items (DropdownMenu*, SelectItem).
 * These items sit in a container that manages keyboard focus itself
 * (reka-ui, roving focus: only one item is reachable via Tab, arrow
 * keys move between them). Instead of a ring, the active item gets a
 * filled highlight. Component-specific additions (destructive variant,
 * descendant colours) stay local.
 */
export const focusHighlight = 'outline-hidden focus:bg-accent focus:text-accent-foreground'

/**
 * List transition properties explicitly (no `transition-all`) so layout
 * properties are not animated. `box-shadow` is intentionally part of
 * the list — Tailwind rings are box-shadows.
 */
export const transitionInteractive =
  'transition-[color,background-color,border-color,box-shadow,outline-color,opacity,transform] duration-200 ease-out'

/**
 * Offset focus ring for card-shaped controls whose inner control holds
 * the focus (FormRadioField variant `card`, card checkbox). The card
 * shows the ring as soon as the control inside is focused — the control
 * itself gives up its own ring via `focusRingResetOffset`. Rationale:
 * the whole card is the hit area, so a ring around the 16 px circle in
 * the corner would be hard to locate during keyboard navigation.
 */
export const focusRingCard =
  'outline-hidden has-[[data-slot=radio-group-item]:focus-visible]:border-ring has-[[data-slot=radio-group-item]:focus-visible]:ring-ring/50 has-[[data-slot=radio-group-item]:focus-visible]:ring-3 has-[[data-slot=radio-group-item]:focus-visible]:ring-offset-2 has-[[data-slot=radio-group-item]:focus-visible]:ring-offset-background has-[[data-slot=checkbox]:focus-visible]:border-ring has-[[data-slot=checkbox]:focus-visible]:ring-ring/50 has-[[data-slot=checkbox]:focus-visible]:ring-3 has-[[data-slot=checkbox]:focus-visible]:ring-offset-2 has-[[data-slot=checkbox]:focus-visible]:ring-offset-background'

/**
 * Counterpart to `focusRingCard`: removes ring and offset from the
 * control sitting inside a card that already shows the focus state.
 */
export const focusRingResetOffset =
  'focus-visible:ring-0 focus-visible:ring-offset-0 aria-invalid:ring-0'

/**
 * Offset focus ring for card-shaped links (recipe card, meal card).
 * The whole card is the hit area, but only the title is the link — the
 * ring therefore belongs on the card, not on the two-line title text,
 * where a ring would be torn apart across the line break. The link
 * itself gives up its outline via `focusRingResetLink`.
 *
 * Unlike `focusRingCard` this does not touch `border-*`: Card draws its
 * hairline with `ring-1 ring-foreground/10`, so the focus utilities
 * override that ring instead of an unused border.
 */
export const focusRingCardLink =
  'outline-hidden has-[[data-slot=card-link]:focus-visible]:ring-ring/50 has-[[data-slot=card-link]:focus-visible]:ring-3 has-[[data-slot=card-link]:focus-visible]:ring-offset-2 has-[[data-slot=card-link]:focus-visible]:ring-offset-background'

/**
 * Counterpart to `focusRingCardLink`: the card shows the focus state,
 * the link inside does not. `outline-hidden` rather than `outline-none`
 * keeps the system outline in forced-colours mode.
 */
export const focusRingResetLink = 'outline-hidden'

/**
 * Hover and active state for card-shaped links, on top of
 * `focusRingCardLink`. Both are gated on the presence of a
 * `data-slot="card-link"` descendant, so cards without a link stay
 * static. `ring-*` rather than `border-*` because Card draws its
 * hairline with `ring-1`. Tailwind wraps `hover:` in
 * `@media (hover: hover)`, so touch devices are unaffected.
 */
export const interactiveCardLink = `${focusRingCardLink} has-[[data-slot=card-link]]:hover:ring-ring has-[[data-slot=card-link]]:hover:-translate-y-0.5 has-[[data-slot=card-link]]:active:translate-y-0`
