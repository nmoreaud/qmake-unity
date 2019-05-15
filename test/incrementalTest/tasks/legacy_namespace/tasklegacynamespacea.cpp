#include "tasklegacynamespacea.h"

#include "factory.h"
#include <QDebug>

using namespace LegacyNamespaceA;

REGISTER_CLASS(TaskLegacyNamespaceA)

void TaskLegacyNamespaceA::Exec()
{
    qDebug() << metaObject()->className() << ", namespace " << NamespaceName();
}

QString LegacyNamespaceA::NamespaceName() { return "A"; }
