#pragma once

#include "task.h"

namespace LegacyNamespaceA
{
    class TaskLegacyNamespaceA : public Task
    {
        Q_OBJECT

    public:
        void Exec() override;
    };

    // function name conflict in unrelated namespaces
    QString NamespaceName();
}
