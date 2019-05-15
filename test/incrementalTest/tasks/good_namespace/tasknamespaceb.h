#pragma once

#include "task.h"

// classes in "GoodNamespace" should be grouped by qmake-unity
namespace GoodNamespace
{
    class TaskNamespaceB : public Task
    {
        Q_OBJECT
    };
}
