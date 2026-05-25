/**
 * Returns true if the string is a valid Bolivian CI (cédula de identidad).
 * Accepts 5–10 digits, optionally followed by a hyphen and a letter (ej. 1234567-1A).
 */
export function isValidCI(ci: string): boolean {
  return /^\d{5,10}(-[A-Z0-9])?$/.test(ci.trim().toUpperCase())
}

/**
 * Returns true if the value is a valid e-mail address.
 */
export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())
}

/**
 * Returns true if the phone number contains 7–15 digits (optionally prefixed by +).
 */
export function isValidPhone(phone: string): boolean {
  return /^\+?\d{7,15}$/.test(phone.trim())
}

/**
 * Returns true if the password meets minimum security requirements:
 * at least 8 characters, one uppercase, one lowercase and one digit.
 */
export function isStrongPassword(password: string): boolean {
  return password.length >= 8 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /\d/.test(password)
}

/**
 * Returns true if the string is not empty after trimming.
 */
export function isRequired(value: string | null | undefined): boolean {
  return !!value && value.trim().length > 0
}
