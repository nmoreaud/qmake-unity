#ifndef SPIDERCREATOR_H
#define SPIDERCREATOR_H

#include <vector>

#include "qge/EntityCreator.h"

namespace qge{
    class CItemDropper;
}

/// An EntityCreator that will create a spider.
/// You can specify the group the spider will be created for as well as the enemy groups of the created spider.
class SpiderCreator : public qge::EntityCreator
{
public:
    SpiderCreator();

    qge::Entity* createEntity() override;
private:
    qge::CItemDropper* itemDropper_;
};

#endif
