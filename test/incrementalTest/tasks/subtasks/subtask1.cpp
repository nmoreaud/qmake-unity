#include "subtask1.h"

#include "factory.h"
#include <QDebug>

// Not included from a directory in the INCLUDE PATH nor with a path relative to the top directory
#include "subtask2.h"

REGISTER_CLASS(SubTask1)

void SubTask1::Exec()
{
    qDebug() << "SubTask1";

    SubTask2 aSub2;
    connect(this, SIGNAL(TriggerTask2()), &aSub2, SLOT(ShowSubTask2()));
    emit TriggerTask2();
}
