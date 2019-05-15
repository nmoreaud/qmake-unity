#include "../tasks/task1.h"

#include "factory.h"
#include <QDebug>

REGISTER_CLASS(Task1)

void Task1::Exec()
{
    qDebug() << "Task1";
}
