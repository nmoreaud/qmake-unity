#include "factory.h"

#include "task.h"

#include <QDebug>

Factory* Factory::_instance;

Factory::Factory()
{
}

Factory &Factory::Instance()
{
    if (_instance == nullptr) {
        _instance = new Factory();
    }
    return *_instance;
}

void Factory::AddTask(QString iName, Task *iTask)
{
    //qDebug() << "register " << iName;
    assert(_tasks.contains(iName) == false);
    _tasks.insert(iName, iTask);
}

QMap<QString, Task *> Factory::GetTasks() const
{
    return _tasks;
}
