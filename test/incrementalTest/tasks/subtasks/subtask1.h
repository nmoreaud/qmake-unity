#ifndef SUBTASK1
#define SUBTASK1

#include "task.h"

class SubTask1 : public Task
{
    Q_OBJECT

public:
    void Exec() override;

signals:
    void TriggerTask2();
};

#endif
