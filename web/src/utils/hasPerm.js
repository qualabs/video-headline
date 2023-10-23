export function isSuperuser (user) {
  return user && user.is_superuser
}

export function hasSupervisorPerm (user) {
  return user && (user.is_superuser)
}

export function hasOperatorPerm (user) {
  return user && (user.is_operator)
}
