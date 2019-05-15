#include "task.h"

#include <QDebug>

Task::Task()
{   
}

Task::~Task()
{
}

void Task::Exec()
{
    qDebug() << metaObject()->className();
}
