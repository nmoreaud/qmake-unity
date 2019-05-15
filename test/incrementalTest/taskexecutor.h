#ifndef TASKEXECUTOR_H
#define TASKEXECUTOR_H

#include <QObject>

class TaskExecutor : public QObject
{
    Q_OBJECT

public:
    TaskExecutor();

public slots:
    void Exec();
};

#endif // TASKEXECUTOR_H
