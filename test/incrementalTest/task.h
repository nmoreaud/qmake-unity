#ifndef TASK_H
#define TASK_H

#include <QObject>

class Task : public QObject
{
    Q_OBJECT

public:
    Task();
    virtual ~Task();

    virtual void Exec();
};

#endif // TASK_H
