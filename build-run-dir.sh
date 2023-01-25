#!/bin/bash
RED='\033[0;31m'
NC='\033[0m'

# Check if we need to build for a registry:
if [ -z "$BUILD_REGISTRY" ]; then
    echo -e "${RED}BUILD_REGISTRY is not set${NC}"
    echo -e "${RED}Building without registry prefix${NC}\n"
else
    # Remove trailing slash:
    BUILD_REGISTRY=$(echo "${BUILD_REGISTRY}" | sed 's:/*$::')
    echo -e "${RED}Building with registry prefix: ${BUILD_REGISTRY}/demo-app:ID${NC}\n"
fi


# Derive the directory which needs to be build based on start ID.
set -e
dir=$(find . -maxdepth 1 -name "${1}*python_app*")

if [ ! -d "$dir" ]; then
    echo "Directory starting with \"${1}\" does not exist."
    exit 1
fi

# Building the image
cd $dir
id=$(echo "$dir" | cut -d'/' -f2 | cut -d'_' -f1 )

if [ -z "$BUILD_REGISTRY" ]; then
    image_name="demo-app:$id"
else
    image_name="${BUILD_REGISTRY}/demo-app:$id"
fi

echo -e "${RED}Build $dir as ${image_name}.${NC}\n"
docker build -t $image_name .

# Function to run the image on a k8s cluster as pod
#    wait for it to run
#    if a key is pressed delete pod, if f is pressed force delete pod

run_k8s () {
    echo -e "${RED}Starting pod demo-app-$id on kubernetes $dir ${NC}\n"
    kubectl run demo-app-$id  --image=$image_name --image-pull-policy=Never --restart=Never
    kubectl wait --for=condition=Ready pod/demo-app-$id
    read -n1 -r -p "Press f to force, else to delete gracefully..." key

    if [ "$key" = 'f' ]; then
        kubectl delete pod demo-app-$id --grace-period=0 --force
    else
        kubectl delete pod demo-app-$id
    fi
}


# Divide the run into two parts, one for general k8s (default), kind k8s (with upload image) and one for docker
if [ "$2" == "docker" ]; then
    echo -e "${RED}Starting container demo-app-$id from $dir ${NC}\n"
    docker run --rm -p 8080:8080 --name demo-app-$id $image_name
elif [ "$2" == "kind" ]; then
    echo -e "${RED}Uploading image to kind $image_name ${NC}\n"
    kind load docker-image $image_name
    run_k8s
elif [ "$2" == "registry" ]; then
    echo -e "${RED}Uploading image to registry $image_name ${NC}\n"
    docker push $image_name
    run_k8s
elif [ "$2" == "norun" ]; then
    echo -e "${RED}Skip running image ${NC}\n"
else
    run_k8s
fi
