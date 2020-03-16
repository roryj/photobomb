package main

import (
	"fmt"
	"image"
	_ "image/jpeg"
	"image/png"
	"log"
	"os"

	"github.com/anthonynsimon/bild/blend"
	"github.com/urfave/cli/v2"
)

func main() {
	app := &cli.App{
		Name:  "capture",
		Usage: "find all the faces in a picture",
		Flags: []cli.Flag{
			&cli.StringFlag{
				Name:     "filePath",
				Aliases:  []string{"f"},
				Usage:    "the full file path for the image",
				Required: true,
			},
			&cli.StringFlag{
				Name:     "outputFile",
				Aliases:  []string{"o"},
				Usage:    "the name of the output file",
				Required: true,
			},
		},
		Action: func(c *cli.Context) error {
			log.Println("starting image processing!")

			inputFilePath := c.String("filePath")
			outputfile := c.String("outputFile")
			if inputFilePath == "" {
				return fmt.Errorf("the filePath passed in was empty. Must be a valid filepath")
			}
			if outputfile == "" {
				return fmt.Errorf("the outputFile passed in was empty. Must be a valid name")
			}

			log.Printf("input file path %s\n", inputFilePath)
			log.Printf("output file %s\n", outputfile)

			s, err := os.Stat(inputFilePath)
			if err != nil {
				if os.IsNotExist(err) {
					return fmt.Errorf("the file at the path '%s' does not exist", inputFilePath)
				}
				return err
			}

			if s.IsDir() {
				return fmt.Errorf("the path '%s' is a directory, not a file", inputFilePath)
			}

			i, err := openImage(inputFilePath)
			if err != nil {
				return err
			}

			// r, err := findFaces(i)
			// if err != nil {
			// 	return err
			// }

			r, err := attempt2(i)
			if err != nil {
				return err
			}

			f, err := os.Create(outputfile)
			if err != nil {
				return err
			}
			defer f.Close()

			return png.Encode(f, r)
		},
	}

	err := app.Run(os.Args)
	if err != nil {
		log.Fatal(err)
	}
}

func openImage(path string) (image.Image, error) {
	log.Printf("loading file '%s'", path)
	imageFile, err := os.Open(path)
	if err != nil {
		return image.Black, err
	}
	log.Println("loading the file was successful")

	i, _, err := image.Decode(imageFile)
	return i, err
}

func attempt2(img image.Image) (image.Image, error) {
	log.Printf("attempting to merge og image with spooky image")
	spooky, err := openImage("/Users/roryjacob/develop/photo-manipulation/ghost2.jpg")
	if err != nil {
		return img, err
	}

	return blend.Opacity(img, spooky, 0.5), nil
}

// given an image, put red rectangles around them
// func findFaces(img image.Image) (image.Image, error) {
// 	fmt.Printf("bounds of image: %d x %d\n", img.Bounds().Dx(), img.Bounds().Dy())

// 	// put
// 	rect := image.Rect(10, 10, img.Bounds().Dx()-10, img.Bounds().Dy()-10)
// 	rect2 := image.Rect(15, 15, img.Bounds().Dx()-15, img.Bounds().Dy()-15)

// 	i := image.NewRGBA64(img.Bounds())

// 	// create the detection doc the same size as the image
// 	boundMask := image.NewRGBA64(img.Bounds())

// 	// for each location, put black and then white smaller
// 	draw.Draw(boundMask, rect, &image.Uniform{color.Black}, image.Point{}, draw.Src)
// 	draw.Draw(boundMask, rect2, &image.Uniform{color.White}, image.Point{}, draw.Src)

// 	// now draw on the main image using the mask
// 	red := color.RGBA{255, 0, 0, 1}
// 	draw.DrawMask(i, rect, &image.Uniform{red}, image.Point{}, boundMask, image.Point{}, draw.Src)

// 	return i, nil
// }
