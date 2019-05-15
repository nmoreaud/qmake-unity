#include "singletask.h"

#include "factory.h"

#include <QDebug>

// this file should not be grouped, because it contains a conflicting macro...
//   @NO_UNITY

REGISTER_CLASS(SingleTask)

#define Task ConflictingMacro
