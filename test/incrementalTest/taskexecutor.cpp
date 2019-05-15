#include "taskexecutor.h"

#include <QCoreApplication>
#include <QDebug>

#include "factory.h"
#include "task.h"

TaskExecutor::TaskExecutor()
{
}

void TaskExecutor::Exec()
{
    qDebug() << Factory::Instance().GetTasks().keys();
    for (Task *task : Factory::Instance().GetTasks())
    {
        task->Exec();
    }

    qApp->exit();
}
