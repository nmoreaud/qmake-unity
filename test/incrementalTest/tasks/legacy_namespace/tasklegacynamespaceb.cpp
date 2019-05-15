#include "tasklegacynamespaceb.h"

#include "factory.h"
#include <QDebug>

using namespace LegacyNamespaceB;

REGISTER_CLASS(TaskLegacyNamespaceB)

void TaskLegacyNamespaceB::Exec()
{
    qDebug() << metaObject()->className() << ", namespace " << NamespaceName();
}

QString LegacyNamespaceB::NamespaceName() { return "B"; }
